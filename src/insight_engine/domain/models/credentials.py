from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from insight_engine.domain.models.enums import OnboardingStage, ApiMode
from insight_engine.serialization.serializable import Serializable


@dataclass
class Credentials(Serializable):
    user_id: UUID
    tenant_id: UUID
    api_key_id: UUID
    scopes: list[str]  # Condensed list of permissions e.g. rules.custom.read
    username: str  # Handle to reference the user (name) in a human-readable way
    api_key_fingerprint: str  # Handle to reference the key (fingerprint) in a human-readable way
    tenant: str  # Handle to reference the tenant (slug) in a human-readable way
    customer: str  # Handle to use for the 'customer' data field
    tenant_ancestors: list[str]  # Ancestor tentant slugs, ordered top-down
    tenant_descendants: dict[
        str, Any]  # Descendant tenant slugs in a dict tree, e.g. {'child1': {}, 'child2': {'child2a': [], 'child2b': []}}
    onboarding_stage: OnboardingStage = field(metadata={'by_value': True})
    api_mode: ApiMode = field(metadata={'by_value': True})
    # Since credentials are only used within a trust boundary of internal services, they do not need verification.
    # We still include an expiry marker for debugging purposes, as there is no need to use them beyond this time.
    expires_on: datetime | None = None

    def can_read_user(self):
        return 'common.users.read' in self.scopes

    def can_read_tenant(self):
        return 'common.tenants.read' in self.scopes

    def can_write_tenant(self):
        return 'common.tenants.write' in self.scopes

    def can_read_subtenants(self):
        return 'common.subtenants.read' in self.scopes

    def can_write_subtenants(self):
        return 'common.subtenants.write' in self.scopes

    def can_write_tableau_id(self):
        return 'common.permissions.write' in self.scopes
