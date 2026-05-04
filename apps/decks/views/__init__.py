# views/__init__.py — re-exports all view classes so urls.py imports stay clean.

from .crud import DeckListView, DeckDetailView, DeckBulkDeleteView
from .upload import DeckUploadView
from .crm import DeckCrmStatusView, FounderContactView, CallNotesView
from .questions import QuestionsView, DeckEmailView
from .comments import CommentListView, CommentDeleteView
from .materials import DeckMaterialView, DeckMaterialDeleteView
from .notes import DeckNoteView, DeckNoteDeleteView
from .auto_answer import AutoAnswerView
from .suggest_questions import SuggestQuestionsView
from .insight import DealInsightView
