from setuptools import setup, find_packages

setup(
    name="idun-playground",
    version="0.1.0",
    description="Dark-mode Azure AI Foundry playground for the NatureLM-Idun-5-MoE agent",
    long_description=(
        "Local stdlib HTTP playground (router.py) + dark Foundry-style UI that "
        "surfaces the full agent trajectory of the NatureLM-Idun-5-MoE tool agent."
    ),
    long_description_content_type="text/markdown",
    py_modules=["router"],
    python_requires=">=3.8",
    # router.py imports idun (idun-sdk). Pin the SDK-parity version.
    install_requires=["idun-sdk>=0.1.21"],
    keywords=["azure", "ai-foundry", "agent", "tool-agent", "playground", "idun"],
)
