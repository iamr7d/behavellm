import os
import random
import time
from datetime import datetime
import logging
from git import Repo
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_commits.log'),
        logging.StreamHandler()
    ]
)

class GitHubAutoCommitter:
    def __init__(self, repo_path, target_file):
        self.repo_path = repo_path
        self.target_file = target_file
        self.repo = Repo(repo_path)
        self.daily_commits = 0
        self.max_daily_commits = random.randint(8, 25)
        
        # Configure git user
        with self.repo.config_writer() as git_config:
            git_config.set_value('user', 'email', 'rahulrajpvr7d.here@gmail.com')
            git_config.set_value('user', 'name', 'rahulrajpvr7d')

    def modify_file(self, add_comma=True):
        try:
            with open(self.target_file, 'r') as file:
                content = file.read().strip()

            new_content = content + ", " if add_comma else content.rstrip(", ")

            with open(self.target_file, 'w') as file:
                file.write(new_content)

            return True
        except Exception as e:
            logging.error(f"Error modifying file: {str(e)}")
            return False

    def commit_changes(self, message):
        try:
            self.repo.index.add([self.target_file])
            self.repo.index.commit(message)
            origin = self.repo.remote('origin')
            origin.push()
            return True
        except Exception as e:
            logging.error(f"Error committing changes: {str(e)}")
            return False

    def make_random_commit(self):
        if self.daily_commits >= self.max_daily_commits:
            logging.info("Daily commit limit reached")
            return

        current_hour = datetime.now().hour
        if not (9 <= current_hour <= 23):  # Only commit between 9 AM and 11 PM
            return

        add_comma = random.choice([True, False])
        action = "Adding" if add_comma else "Removing"
        
        if self.modify_file(add_comma):
            if self.commit_changes(f"{action} comma - Auto commit"):
                self.daily_commits += 1
                logging.info(f"Successfully made commit {self.daily_commits}/{self.max_daily_commits}")
                
                # Schedule next commit
                wait_time = random.randint(1800, 7200)  # 30 mins to 2 hours
                schedule.every(wait_time).seconds.do(self.make_random_commit).tag('commit_job')

    def reset_daily_counter(self):
        self.daily_commits = 0
        self.max_daily_commits = random.randint(8, 25)
        logging.info(f"Reset daily counter. New max commits: {self.max_daily_commits}")

def main():
    # Replace these with your actual paths
    REPO_PATH = "PATH_TO_YOUR_REPO"  # e.g., "C:/Users/username/my_repo"
    TARGET_FILE = "PATH_TO_TARGET_FILE"  # e.g., "C:/Users/username/my_repo/commit_file.txt"

    committer = GitHubAutoCommitter(REPO_PATH, TARGET_FILE)
    
    # Schedule daily reset at midnight
    schedule.every().day.at("00:00").do(committer.reset_daily_counter)
    
    # Initial commit
    committer.make_random_commit()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
