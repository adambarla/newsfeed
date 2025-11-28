import pytest
from newsfeed.classification import GeminiNewsClassifier
from newsfeed.models import NewsCategory
from newsfeed.config import get_settings


def has_api_key():
    try:
        settings = get_settings()
        return bool(settings.GEMINI_API_KEY)
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(not has_api_key(), reason="GEMINI_API_KEY not set")
class TestGeminiNewsClassifierIntegration:
    @pytest.fixture
    def classifier(self):
        return GeminiNewsClassifier()

    @pytest.mark.asyncio
    async def test_ai_emerging_tech(self, classifier):
        text = """
        OpenAI has released a new version of GPT-4 that is significantly faster and cheaper.
        The new model, GPT-4o, demonstrates improved capabilities in reasoning and coding.
        Developers can access it via the API starting today.
        """
        category = await classifier.classify(text)
        print(f"AI Text classified as: {category}")
        assert category == NewsCategory.AI_EMERGING_TECH

    @pytest.mark.asyncio
    async def test_cybersecurity(self, classifier):
        text = """
        A critical vulnerability has been found in the Linux kernel.
        Attackers can exploit this zero-day to gain root privileges.
        Security researchers advise patching immediately.
        """
        category = await classifier.classify(text)
        print(f"Cybersecurity Text classified as: {category}")
        assert category == NewsCategory.CYBERSECURITY

    @pytest.mark.asyncio
    async def test_software_development(self, classifier):
        text = """
        Python 3.13 introduces a JIT compiler that significantly improves performance.
        The Global Interpreter Lock (GIL) can now be disabled in experimental mode.
        Many developers are excited about the multi-threading capabilities.
        """
        category = await classifier.classify(text)
        print(f"Software Text classified as: {category}")
        assert category == NewsCategory.SOFTWARE_DEVELOPMENT

    @pytest.mark.asyncio
    async def test_hardware_devices(self, classifier):
        text = """
        NVIDIA has announced its new RTX 5090 graphics card with 32GB VRAM.
        The new GPU features improved ray tracing cores and lower power consumption.
        Gamers and creators are eager to test the new hardware benchmarks.
        """
        category = await classifier.classify(text)
        print(f"Hardware Text classified as: {category}")
        assert category == NewsCategory.HARDWARE_DEVICES

    @pytest.mark.asyncio
    async def test_tech_industry_business(self, classifier):
        text = """
        Microsoft's stock reached an all-time high after the latest earnings report.
        The company reported 20% growth in cloud revenue driven by Azure.
        Analysts predict continued dominance in the enterprise sector.
        """
        category = await classifier.classify(text)
        print(f"Business Text classified as: {category}")
        assert category == NewsCategory.TECH_INDUSTRY_BUSINESS

    @pytest.mark.asyncio
    async def test_other_category(self, classifier):
        text = """
        The local bakery won an award for the best croissant in the city.
        The judges praised the flaky texture and buttery flavor.
        It has been a staple in the community for 20 years.
        """
        category = await classifier.classify(text)
        print(f"Other Text classified as: {category}")
        assert category == NewsCategory.OTHER

    @pytest.mark.asyncio
    async def test_ambiguous_crypto(self, classifier):
        # Crypto often falls under emerging tech or business/other depending on context
        # This test ensures it doesn't crash and returns *a* valid category
        text = """
        Bitcoin prices surged past $100,000 today amid new regulatory approvals.
        Institutional investors are pouring money into the ETF.
        """
        category = await classifier.classify(text)
        print(f"Crypto Text classified as: {category}")
        assert category in [
            NewsCategory.TECH_INDUSTRY_BUSINESS,
            NewsCategory.AI_EMERGING_TECH,
            NewsCategory.OTHER,
        ]

    @pytest.mark.asyncio
    async def test_ambiguous_robotics(self, classifier):
        text = """
        Boston Dynamics revealed a new electric Atlas robot.
        It features 360-degree joints and can perform complex parkour.
        """
        category = await classifier.classify(text)
        print(f"Robotics Text classified as: {category}")
        # Could be hardware or AI/Emerging
        assert category in [
            NewsCategory.HARDWARE_DEVICES,
            NewsCategory.AI_EMERGING_TECH,
        ]
