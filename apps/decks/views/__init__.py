# views/__init__.py — re-exports all view classes so urls.py imports stay clean.

from .crud import DeckListView, DeckDetailView, DeckBulkDeleteView
from .upload import DeckUploadView
from .crm import DeckCrmStatusView, FounderContactView, CallNotesView
from .questions import QuestionsView, DeckEmailView
from .comments import CommentListView, CommentDeleteView
from .materials import DeckMaterialView, DeckMaterialDeleteView
from .auto_answer import AutoAnswerView
