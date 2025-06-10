import pandas as pd
import os
from typing import Dict, List, Optional
from datetime import datetime
from llm_agents import ContentOptimizer, ModelConfig

class ContentOptimizerExperiment:
    """Class to run experiments with the ContentOptimizer."""
    
    def __init__(
        self,
        input_file: str,
        output_dir: str = "test_results",
        polisher_config: ModelConfig = None,
        critic_config: ModelConfig = None
    ):
        """
        Initialize the experiment.
        
        Args:
            input_file (str): Path to input CSV file
            output_dir (str): Directory to save results
            polisher_config (ModelConfig): Configuration for content polisher
            critic_config (ModelConfig): Configuration for content critic
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.optimizer = ContentOptimizer(
            polisher_config=polisher_config or ModelConfig(temperature=0.8),
            critic_config=critic_config or ModelConfig(temperature=0.3)
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def optimize_content(self, content: str, content_type: str = "experience", job_description: Optional[str] = None) -> str:
        """
        Optimize a single piece of content.
        
        Args:
            content (str): Content to optimize
            content_type (str): Type of content (summary, skills, experience, projects)
            job_description (Optional[str]): Job description for optimization context
            
        Returns:
            str: Optimized content
        """
        try:
            return self.optimizer.optimize_content(
                content=content,
                content_type=content_type,
                job_description=job_description
            )
        except Exception as e:
            print(f"Error optimizing {content_type}: {str(e)}")
            return content  # Return original content if optimization fails
            
    def run_experiment(self) -> None:
        """Run the optimization experiment on all entries in the input file."""
        # Read input CSV
        df = pd.read_csv(self.input_file)
        
        # Initialize columns for optimized content
        df['optimized_summary'] = None
        df['optimized_skills'] = None
        df['optimized_work_experience'] = None
        df['optimized_projects'] = None
        
        # Process each row
        for idx, row in df.iterrows():
            print(f"Processing entry {idx + 1}/{len(df)}...")
            
            # Optimize each section
            df.at[idx, 'optimized_summary'] = self.optimize_content(
                content=row['summary'],
                content_type='summary',
                job_description=row['job_description']
            )
            
            df.at[idx, 'optimized_skills'] = self.optimize_content(
                content=row['skills'],
                content_type='skills',
                job_description=row['job_description']
            )
            
            df.at[idx, 'optimized_work_experience'] = self.optimize_content(
                content=row['work_experience'],
                content_type='experience',
                job_description=row['job_description']
            )
            
            if pd.notna(row['projects']):  # Only optimize projects if they exist
                df.at[idx, 'optimized_projects'] = self.optimize_content(
                    content=row['projects'],
                    content_type='projects',
                    job_description=row['job_description']
                )
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"optimization_results_{timestamp}.csv")
        df.to_csv(output_file, index=False)
        print(f"Results saved to: {output_file}")

def main():
    """Main function to run the experiment."""
    # Configure the experiment
    experiment = ContentOptimizerExperiment(
        input_file="test_data.csv",  # You should create this file
        output_dir="test_results",
        polisher_config=ModelConfig(temperature=0.8),
        critic_config=ModelConfig(temperature=0.3)
    )
    
    # Run the experiment
    experiment.run_experiment()

if __name__ == "__main__":
    main() 