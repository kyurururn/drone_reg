from setuptools import setup

setup(
    name='TelloDrone',
    version='0.1',
    py_modules=['TelloDrone_Lib'],  # ファイル名（拡張子は不要）
    install_requires=[
        'opencv-python',
        'numpy',
    ],
)
