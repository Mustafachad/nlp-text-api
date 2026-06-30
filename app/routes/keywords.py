import spacy
from fastapi import APIRouter
from app.models import TextRequest, KeywordsResponse, Entity

router = APIRouter()

# Load the model once when the module is imported, not on every request.
# en_core_web_sm is a small English pipeline that includes a tokeniser,
# POS tagger, dependency parser, and NER model trained on web text.
nlp = spacy.load("en_core_web_sm")

# Entity types we care about for a general-purpose keywords endpoint.
# Full label list: https://spacy.io/api/annotation#named-entities
_ENTITY_TYPES = {"PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT"}


@router.post("/keywords", response_model=KeywordsResponse, tags=["NLP"])
def extract_keywords(request: TextRequest):
    """
    Extracts keywords and named entities from the submitted text.

    - **keywords** — unique nouns and proper nouns that are not stop words or
      punctuation. Frequency-ranked so the most common content words appear first.
    - **entities** — named entities recognised by spaCy's NER model, filtered to
      people, organisations, places, products, and events.
    """
    doc = nlp(request.text)

    # --- Keywords ---
    # We treat nouns (NOUN) and proper nouns (PROPN) as content words.
    # spaCy's POS tagger assigns these based on syntactic context, which is
    # more reliable than a naive frequency count over all tokens.
    # token.lemma_ gives the base form ("running" → "run", "APIs" → "api")
    # so we don't count the same word twice under different surface forms.
    freq: dict[str, int] = {}
    for token in doc:
        if (
            token.pos_ in {"NOUN", "PROPN"}
            and not token.is_stop
            and not token.is_punct
            and not token.is_space
            and len(token.text) > 1
        ):
            lemma = token.lemma_.lower()
            freq[lemma] = freq.get(lemma, 0) + 1

    # Sort by frequency descending so the most prominent words come first.
    keywords = [word for word, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)]

    # --- Named entities ---
    # doc.ents is the list of entity spans identified by the NER model.
    # ent.text is the raw surface form; ent.label_ is the entity type.
    # We deduplicate on (text, label) so the same entity isn't listed twice.
    seen: set[tuple[str, str]] = set()
    entities: list[Entity] = []
    for ent in doc.ents:
        if ent.label_ in _ENTITY_TYPES:
            key = (ent.text.strip(), ent.label_)
            if key not in seen:
                seen.add(key)
                entities.append(Entity(text=ent.text.strip(), label=ent.label_))

    return KeywordsResponse(keywords=keywords, entities=entities)
