import click
from .project import Project
from .config import load_config
import os

@click.group()
def cli():
    """Auteur Studio - AI-powered animation pipeline."""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--config', default=None, help='Path to config file.')
def init(project_name, config):
    """Initialize a new project."""
    cfg = load_config(config)
    project = Project(project_name, cfg)
    project.initialize()
    click.echo(f"Project {project_name} initialized at {project.project_root}.")

@cli.command()
@click.argument('project_name')
@click.option('--prompt', required=True, help='The story prompt.')
@click.option('--config', default=None, help='Path to config file.')
def generate_story(project_name, prompt, config):
    """Generate a story for the project."""
    cfg = load_config(config)
    project = Project(project_name, cfg)
    project.generate_story(prompt)
    click.echo(f"Story generated for {project_name}.")

@cli.command()
@click.argument('project_name')
@click.option('--config', default=None, help='Path to config file.')
def generate_audio(project_name, config):
    """Generate audio for the project."""
    cfg = load_config(config)
    project = Project(project_name, cfg)
    project.generate_audio()
    click.echo(f"Audio generated for {project_name}.")

@cli.command()
@click.argument('project_name')
@click.option('--config', default=None, help='Path to config file.')
def generate_animation(project_name, config):
    """Generate animation for the project."""
    cfg = load_config(config)
    project = Project(project_name, cfg)
    project.generate_animation()
    click.echo(f"Animation generated for {project_name}.")

@cli.command()
@click.argument('project_name')
@click.option('--output', default="final_video.mp4", help='Output video filename.')
@click.option('--config', default=None, help='Path to config file.')
def compile_video(project_name, output, config):
    """Compile the video for the project."""
    cfg = load_config(config)
    project = Project(project_name, cfg)
    video_path = project.compile_video(output)
    click.echo(f"Video compiled: {video_path}")

@cli.command()
@click.argument('project_name')
@click.option('--prompt', required=True, help='The story prompt.')
@click.option('--output', default="final_video.mp4", help='Output video filename.')
@click.option('--config', default=None, help='Path to config file.')
def generate(project_name, prompt, output, config):
    """Run the entire pipeline: story, audio, animation, video."""
    cfg = load_config(config)
    project = Project(project_name, cfg)
    project.initialize()
    project.generate_story(prompt)
    project.generate_audio()
    project.generate_animation()
    video_path = project.compile_video(output)
    click.echo(f"Video compiled: {video_path}")

if __name__ == '__main__':
    cli()