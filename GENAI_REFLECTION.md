# Generative AI Reflection – COMP3011 Coursework 2

## AI Tools Used

- **GitHub Copilot** – used directly within VS Code throughout development for inline code suggestions and docstring generation.
- **ChatGPT (GPT-4)** – used for higher-level discussions around project structure, library selection, and test strategy.

## Where AI Helped

AI was most useful in the early stages of the project. GitHub Copilot helped scaffold the module structure across `crawler.py`, `indexer.py`, `search.py`, and `storage.py`, keeping the separation of concerns clear from the start. It also suggested using `BeautifulSoup` with the `lxml` parser for HTML extraction and `requests` for fetching pages, both of which were appropriate choices. For testing, ChatGPT helped generate initial unit test outlines for each module, which saved time setting up the `pytest` structure.

## Where AI Was Incorrect or Insufficient

AI suggestions were less reliable when it came to specifics. The initial index structure suggested by ChatGPT did not store token positions, only frequency — this had to be redesigned manually to support the `positions` field required for the assignment. Copilot also occasionally generated overly broad exception handling and did not account for edge cases such as pages with missing `<title>` tags, empty body content, or failed HTTP responses, all of which required manual fixes.

## Debugging and Refinement

Where AI-generated code was incorrect, I traced the failures through the test suite and corrected behaviour directly. For example, the `parse_page` function required an explicit fallback for missing titles after observing test failures on malformed HTML inputs.

## Effect on Learning

Using AI accelerated boilerplate work but required me to critically evaluate every suggestion. Understanding why a suggestion was wrong — particularly around index design and edge-case handling — reinforced my understanding of the underlying concepts more than if I had relied on AI uncritically.
