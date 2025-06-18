use scheduler_sim::{
    FCFSScheduler, generate_jobs, mlfq::*, pri::*, rr::*, simulate, sjf::*, srpt::*,
};
use std::fs::File;
use std::io::Write;

use csv::ReaderBuilder;
use plotters::prelude::*;
use plotters::style::RGBColor;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    // Ensure the directories exist
    std::fs::create_dir_all("benchmarks").unwrap_or_default();
    std::fs::create_dir_all("plots").unwrap_or_default();
    
    let mut results = vec!["
    name,mean_wait,mean_turnaround,utilization,throughput,starvation_rate,max_wait,fairness_index,avg_response_ratio
    ".trim().to_string()];
    
    // Generate a consistent set of jobs for testing
    let job_data = generate_jobs(100, 1.0, 1.25);

    macro_rules! run_scheduler {
        ($name:expr, $sched:expr) => {{
            let mut scheduler = $sched;
            let mut cloned_jobs = job_data.clone();
            let metrics = simulate(&mut scheduler, &mut cloned_jobs, $name);
            println!("{}", metrics);
            results.push(metrics.to_string());
        }};
    }

    // Short clear names for schedulers
    run_scheduler!("FCFS", FCFSScheduler::new());
    run_scheduler!("SJF", SJF::new());
    run_scheduler!("SRPT", SRPT::new());
    run_scheduler!("RR", RR::new(0.1));
    run_scheduler!("PRI", PRI::new());
    run_scheduler!("MLFQ", MLFQ::new());

    let mut file = File::create("benchmarks/output.csv").unwrap();
    for line in results {
        writeln!(file, "{}", line).unwrap();
    }

    let mut rdr = ReaderBuilder::new()
        .has_headers(true)
        .from_path("benchmarks/output.csv")?;
    let rows: Vec<Row> = rdr.deserialize().filter_map(Result::ok).collect();

    // Generate all the plots with descriptive titles
    plot_metric(&rows, "Mean Wait Time (seconds)", "plots/mean_wait.png", |r| r.mean_wait)?;
    plot_metric(&rows, "Mean Turnaround Time (seconds)", "plots/turnaround.png", |r| {
        r.mean_turnaround
    })?;
    plot_metric(&rows, "CPU Utilization (%)", "plots/utilization.png", |r| {
        r.utilization
    })?;
    plot_metric(&rows, "Job Starvation Rate (%)", "plots/starvation.png", |r| {
        r.starvation_rate * 100.0 // Convert to percentage
    })?;
    plot_metric(&rows, "Fairness Index (0-1)", "plots/fairness.png", |r| {
        r.fairness_index
    })?;
    plot_metric(&rows, "Normalized Response Ratio", "plots/response_ratio.png", |r| {
        r.avg_response_ratio
    })?;
    
    println!("All plots generated successfully in the 'plots' directory.");

    Ok(())
}

#[derive(Debug, serde::Deserialize)]
struct Row {
    name: String,
    mean_wait: f64,
    mean_turnaround: f64,
    utilization: f64,
    throughput: f64,
    starvation_rate: f64,
    max_wait: f64,
    fairness_index: f64,
    avg_response_ratio: f64,
}

fn plot_metric<F>(
    rows: &[Row],
    field_name: &str,
    filename: &str,
    extract: F,
) -> Result<(), Box<dyn Error>>
where
    F: Fn(&Row) -> f64,
{
    // Define distinct colors with good contrast for the chart
    let colors = [
        &RGBColor(31, 119, 180),   // Blue
        &RGBColor(255, 127, 14),   // Orange
        &RGBColor(44, 160, 44),    // Green
        &RGBColor(214, 39, 40),    // Red
        &RGBColor(148, 103, 189),  // Purple
        &RGBColor(140, 86, 75),    // Brown
    ];

    // Higher resolution for better quality
    let root = BitMapBackend::new(filename, (1200, 800)).into_drawing_area();
    root.fill(&WHITE)?;

    // Split the drawing area - top 80% for chart, bottom 20% for labels
    let (upper, lower) = root.split_vertically(640);

    let labels: Vec<String> = rows.iter().map(|r| r.name.clone()).collect();
    let values: Vec<f64> = rows.iter().map(|r| extract(r)).collect();

    let y_max = values
        .iter()
        .cloned()
        .fold(f64::NEG_INFINITY, f64::max)
        .max(1.0);

    // Create the main chart in the upper area
    let mut chart = ChartBuilder::on(&upper)
        .caption(field_name, ("sans-serif", 40))
        .margin_top(20)
        .margin_right(40)
        .margin_left(80)
        .margin_bottom(0)  // No bottom margin since we'll put labels below
        .x_label_area_size(0)  // No x-axis labels here
        .y_label_area_size(60)
        .build_cartesian_2d(0f64..labels.len() as f64, 0.0..y_max * 1.2)?;

    chart
        .configure_mesh()
        .disable_x_mesh()
        .y_desc(field_name)
        .y_label_formatter(&|y| format!("{:.2}", y))
        .draw()?;

    // Draw bars with value labels on top
    for (i, &value) in values.iter().enumerate() {
        let i_f64 = i as f64;
        let bar_width = 0.7;  // Width of each bar (70% of available space)
        let x_start = i_f64 + 0.15;  // Center the bar
        let x_end = x_start + bar_width;
        let x_center = x_start + bar_width / 2.0;
        
        // Draw the bar with color from our palette
        let color = colors[i % colors.len()];
        chart.draw_series(std::iter::once(
            Rectangle::new([(x_start, 0.0), (x_end, value)], color.filled())
        ))?;
        
        // Add value label on top of each bar
        chart.draw_series(std::iter::once(
            Text::new(
                format!("{:.2}", value),
                (x_center, value + y_max * 0.03),
                ("sans-serif", 18),
            )
        ))?;
    }

    // Create a separate area for the scheduler labels and color legend
    let mut legend = ChartBuilder::on(&lower)
        .set_all_label_area_size(0)
        .build_cartesian_2d(0f64..1f64, 0f64..1f64)?;

    legend.configure_mesh().disable_mesh().draw()?;

    // Add title for the legend section
    legend.draw_series(std::iter::once(
        Text::new(
            "Scheduler Types",
            (0.5, 0.9),
            ("sans-serif", 25)
        )
    ))?;

    // Draw scheduler names with corresponding color boxes
    for (i, name) in labels.iter().enumerate() {
        let color = colors[i % colors.len()];
        
        // Calculate positions for the legend entries
        // We'll place 3 items per row in the legend
        let row = i / 3;
        let col = i % 3;
        let x = 0.1 + (col as f64) * 0.3;
        let y = 0.7 - (row as f64) * 0.2;
        
        // Draw color box
        legend.draw_series(std::iter::once(
            Rectangle::new([(x, y - 0.05), (x + 0.05, y)], color.filled())
        ))?;
        
        // Draw scheduler name
        legend.draw_series(std::iter::once(
            Text::new(
                name.clone(),
                (x + 0.07, y - 0.025),
                ("sans-serif", 20)
            )
        ))?;
        
        // Draw corresponding bar number (for extra clarity)
        legend.draw_series(std::iter::once(
            Text::new(
                format!("Bar #{}", i+1),
                (x + 0.07, y - 0.07),
                ("sans-serif", 14)
            )
        ))?;
    }

    // Present the final drawing
    root.present()?;

    Ok(())
}
