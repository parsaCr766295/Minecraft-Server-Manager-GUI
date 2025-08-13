from setuptools import setup, find_packages

setup(
    name="minecraft-server-manager",
    version="1.2.1",
    description="A comprehensive tool for managing Minecraft Java Edition servers",
    author="AsanCraft DEv",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.1.2",
        "Pillow>=9.0.0",
        "flask>=2.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        'console_scripts': [
            'mcservermanager=gui_launcher:main',
        ],
    },
    include_package_data=True,
    python_requires='>=3.6',
)