# Content Optimizer Experiments

This directory contains tools for experimenting with the resume content optimizer.

## Files
- `test_content_optimizer.py`: Main experiment module
- `test_data.csv`: Sample input data
- `test_results/`: Directory where results are saved

## Input Format
The input CSV file should have the following columns:
- `summary`: Professional summary
- `skills`: Comma-separated list of skills
- `work_experience`: Work experience (can be multi-line)
- `projects`: Projects (can be multi-line)
- `job_description`: Target job description for optimization

## Running Experiments
1. Prepare your input CSV file following the format in `test_data.csv`
2. Run the experiment:
   ```bash
   python tests/test_content_optimizer.py
   ```
3. Results will be saved in `test_results/` with timestamp in the filename

## Output Format
The output CSV will contain all input columns plus:
- `optimized_summary`
- `optimized_skills`
- `optimized_work_experience`
- `optimized_projects`

## Configuration
You can modify the experiment parameters in `test_content_optimizer.py`:
- `polisher_config`: Controls creativity in optimization (default temperature: 0.8)
- `critic_config`: Controls strictness in evaluation (default temperature: 0.3)
- `input_file`: Path to your input CSV
- `output_dir`: Directory for results 