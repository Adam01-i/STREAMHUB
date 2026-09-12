from abc import ABC, abstractmethod


class AdProvider(ABC):
    """Abstraction pour tout fournisseur publicitaire. L'application ne dépend jamais
    directement d'un fournisseur précis — seulement de cette interface."""

    @abstractmethod
    def is_enabled(self) -> bool:
        """Indique si ce provider a une configuration valide et doit être actif."""

    @abstractmethod
    def render(self, placement: str) -> str | None:
        """Retourne le HTML/script pour cet emplacement, ou None si rien à afficher.
        Ne doit jamais retourner de contenu qui modifie un flux vidéo ou le lecteur."""
