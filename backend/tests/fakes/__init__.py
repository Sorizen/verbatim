from app.providers.protocols import Providers
from tests.fakes.images import FakeImages
from tests.fakes.llm import FakeLlm
from tests.fakes.speech import FakeSpeech
from tests.fakes.videos import FakeVideos


def build_fake_providers(
    *, flaky_submissions: frozenset[int] = frozenset(), failed_submissions: frozenset[int] = frozenset()
) -> Providers:
    return Providers(
        llm=FakeLlm(),
        images=FakeImages(),
        videos=FakeVideos(flaky_submissions=flaky_submissions, failed_submissions=failed_submissions),
        speech=FakeSpeech(),
    )


__all__ = ['FakeImages', 'FakeLlm', 'FakeSpeech', 'FakeVideos', 'build_fake_providers']
