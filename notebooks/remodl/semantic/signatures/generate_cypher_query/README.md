# GenerateCypherQuery

## Description
GenerateCypherQuery is a DSPy signature that transforms natural language statements into Cypher graph database queries. It intelligently extracts entities and relationships from text, integrates with existing graph facts, and generates both primary and supplementary Cypher queries. The signature handles unique node identification via ukid fields, prevents duplicate node creation, and can process both single statements and lists. It supports various input sources including chat messages, agent memories, and knowledge bases, while providing detailed explanations of the extraction and query generation process.

## Usage

### Input Fields

#### Required
- **statement** (str): Natural language text describing entities, relationships, or graph operations
  - Can be a single statement or multiple statements
  - Examples: chat messages, agent memories, knowledge entries

#### Optional
- **facts** (list[str]): Existing Cypher facts related to the statement
  - Default: empty list
  - May support or contradict the statement

- **facts_context** (str): Context explaining fact relevance
  - Default: empty string

### Output Fields

1. **extracted_entities**: List of entities with properties and ukid identifiers
2. **extracted_relationships**: Relationships connecting entities
3. **relevant_facts**: Supporting facts from input that relate to the statement
4. **cypher_query**: Primary Cypher query with inline comments
   - Avoids duplicating nodes (matches by ukid)
   - Includes explanatory comments
5. **additional_cypher_queries**: Supplementary queries for full integration
6. **explanation**: Detailed process description

## Key Features

- **UKID Handling**: Recognizes unique identifiers (format: 'h.dsds.sdsd/sdsd' or 'hdsdsds.*')
- **Duplicate Prevention**: Matches existing nodes before creating new ones
- **Fact Integration**: Aligns or resolves contradictions with existing facts
- **Multi-statement Support**: Processes single or multiple statements

## Example

```python
import dspy

# Initialize the signature
query_generator = dspy.ChainOfThought(GenerateCypherQuery)

# Generate query from statement
result = query_generator(
    statement="Alice works at TechCorp as a software engineer",
    facts=["MATCH (a:Person {ukid: 'h.person.alice/001'}) RETURN a"],
    facts_context="Alice already exists in the graph"
)

# Access outputs
print(result.cypher_query)
print(result.additional_cypher_queries)
print(result.explanation)
```

## Best Practices

1. Provide existing facts when available to prevent duplicates
2. Include facts_context to guide integration logic
3. Review additional_cypher_queries for complete data integration
4. Use the explanation field to understand extraction decisions