from .data import HISTORICAL, SOURCES, sec_companyfacts, latest_quarter_note
def load_data():
    facts,status=sec_companyfacts()
    return HISTORICAL.copy(), SOURCES.copy(), status
