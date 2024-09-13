import subprocess
import os

def compile_scss():
    scss_dir = 'static/scss'
    css_dir = 'static/css'

    if not os.path.exists(scss_dir):
        print(f"Error: SCSS directory '{scss_dir}' does not exist.")
        return

    if not os.path.exists(css_dir):
        os.makedirs(css_dir)

    command = f'sass {scss_dir}: {css_dir}'
    try:
        subprocess.run(command, shell=True, check=True)
        print("SCSS compiled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during SCSS compilation: {e}")

if __name__ == "__main__":
    compile_scss()
