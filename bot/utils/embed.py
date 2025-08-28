import discord

from config import Config


DEFAULT_FOOTER = "Maximally : The global hackathon league"


def base_embed(title: str, description: str | None = None, color: discord.Color | None = None) -> discord.Embed:
    em = discord.Embed(title=title, description=description or discord.Embed.Empty, color=color or discord.Color.blurple())
    if Config.MAXIMALLY_LOGO_URL:
        em.set_thumbnail(url=Config.MAXIMALLY_LOGO_URL)
    em.set_footer(text=DEFAULT_FOOTER)
    return em


def volunteer_task_embed(task_row: dict | discord.utils.MISSING | None):
    if not task_row:
        return base_embed("Volunteer Task", "Task not found.", discord.Color.red())
    claimed_text = (
        f"Claimed by {task_row['claimed_by_username']}" if task_row.get("claimed_by_username") else "Unclaimed"
    )
    title = f"#{task_row['id']} — {task_row['title']}"
    desc = f"Status: {task_row['status']}\n{claimed_text}"
    return base_embed(title, desc, discord.Color.blue())


def volunteer_tasks_list_embed(task_rows):
    em = base_embed("Volunteer Tasks", color=discord.Color.blue())
    if not task_rows:
        em.description = "No tasks yet. Use /volunteer add to create one."
        return em
    for row in task_rows:
        claimed_text = row["claimed_by_username"] if row["claimed_by_username"] else "Unclaimed"
        em.add_field(
            name=f"#{row['id']} — {row['title']}",
            value=f"Status: {row['status']} | {claimed_text}",
            inline=False,
        )
    return em


__all__ = [
    "base_embed",
    "volunteer_task_embed",
    "volunteer_tasks_list_embed",
]

