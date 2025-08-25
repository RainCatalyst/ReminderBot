import asyncio
from dida365 import Dida365Client, ServiceType, TaskCreate, TaskPriority
from config import PROJECT_ID
from datetime import datetime

class TaskAPI:
    def __init__(self):
        self.client = Dida365Client(
            service_type=ServiceType.TICKTICK,
            redirect_uri="http://localhost:8080/callback",
            save_to_env=True
        )

    async def authenticate(self):
        if not self.client.auth.token:
            await self.client.authenticate()

    async def create_task(self, title: str, due_date=None, all_day=False, content: str = ""):
        await self.authenticate()

        task = await self.client.create_task(
            TaskCreate(
                project_id=PROJECT_ID,
                title=title,
                content=content,
                due_date=due_date,
                is_all_day=all_day,
                priority=TaskPriority.NONE
            )
        )
        return task
    
    async def get_todays_tasks(self):
        await self.authenticate()
        project_data = await self.client.get_project_with_data(project_id=PROJECT_ID)
        tasks = []
        today_date = datetime.today().date()
        for task in project_data.tasks:
            if task.start_date != None and task.start_date.date() == today_date:
                tasks.append(task.title)
        return tasks
    
    async def list_projects(self):
        await self.authenticate()
        projects = await self.client.get_projects()
        for project in projects:
            print(f"Project: {project.name} ({project.id})")

# Example usage:
# asyncio.run(TaskManager().create_task("Test Task", "This is a test."))
