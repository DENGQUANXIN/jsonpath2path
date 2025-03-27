import os
import shutil

from setuptools import setup, find_packages, Command


class CleanCommand(Command):
    """自定义清理命令"""
    description = "清理生成的文件和目录"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_dir = 'build'
        dist_dir = 'dist'
        egg_info_dirs = [d for d in os.listdir('.') if d.endswith('.egg-info')]

        # 删除 build 目录
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
            print(f"已删除 {build_dir} 目录")

        # 删除 dist 目录
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
            print(f"已删除 {dist_dir} 目录")

        # 删除所有 .egg-info 目录
        for egg_info_dir in egg_info_dirs:
            if os.path.exists(egg_info_dir):
                shutil.rmtree(egg_info_dir)
                print(f"已删除 {egg_info_dir} 目录")


setup(
    name="jsonpath2path",
    version="0.1.0",
    author="DENGQUANXIN",
    author_email="2507120731@qq.com",
    description="jsonpath2path - JSON Data Transformation Tool.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dengquanxin/jsonpath2path",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=["jsonpath_ng>=1.7.0", "lark>=1.2.2"],
    license="Apache-2.0",
    cmdclass={
        'clean': CleanCommand
    }
)
