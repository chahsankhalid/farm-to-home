from enum import Enum


class ApiMode(Enum):
    SANDBOX = 'sandbox'
    PRODUCTION = 'production'


class OnboardingStage(Enum):
    INTEGRATING = 'integrating'
    LIVE = 'live'
    CHURNED = 'churned'
