class GenerateCypherQuery(dspy.Signature):
    """Generate Cypher queries from natural language statements, extracting entities and relationships while integrating with existing graph facts."""
    
    statement: str = dspy.InputField(
        desc="A natural language statement or list of statements describing entities, relationships, or graph operations. May be from chat messages, memories, knowledge, or other data sources."
    )
    
    facts: list[str] = dspy.InputField(
        default_factory=list,
        desc="Optional existing facts in Cypher format that are related to the statement. May align with or contradict the statement."
    )
    
    facts_context: str = dspy.InputField(
        default="",
        desc="Optional context explaining how the existing facts relate to the statement being processed."
    )
    
    extracted_entities: list[dict[str, str]] = dspy.OutputField(
        desc="Entities extracted from the statement with their properties and ukid identifiers."
    )
    
    extracted_relationships: list[dict[str, str]] = dspy.OutputField(
        desc="Relationships extracted from the statement connecting entities."
    )
    
    relevant_facts: list[str] = dspy.OutputField(
        desc="Supporting or related facts from the provided facts that are relevant to the statement."
    )
    
    cypher_query: str = dspy.OutputField(
        desc="Primary Cypher query to insert or update the graph with extracted entities and relationships. Includes explanatory comments for clarity and avoids duplicating existing nodes (matched by ukid)."
    )
    
    additional_cypher_queries: list[str] = dspy.OutputField(
        desc="Additional Cypher queries needed to fully integrate the statement with existing facts, handle contradictions, or establish supporting relationships."
    )
    
    explanation: str = dspy.OutputField(
        desc="Explanation of the query generation process, including how entities were identified, relationships established, and facts integrated."
    )