# UniMind AI — Limitations

## 1. Model Dependency

UniMind AI depends on the Google Gemini API. Model availability, response time, and free-tier usage quotas may affect application reliability.

**Future improvement:** Support alternative LLM providers and implement robust fallback mechanisms.

## 2. RAG Retrieval Quality

The quality of generated answers depends on the relevance and completeness of retrieved document chunks. Relevant information may not always be retrieved.

**Future improvement:** Experiment with chunk sizes, overlap, hybrid search, and reranking.

## 3. Citation Accuracy

The system validates citation labels against retrieved source positions. This does not guarantee that every citation semantically supports the associated claim.

**Future improvement:** Add semantic citation verification and more comprehensive evaluation.

## 4. Rate Limiting

The current rate limiter uses in-memory storage. Request counts may reset when the backend restarts, and limits are not shared across multiple backend instances.

**Future improvement:** Use Redis or another shared storage system for distributed rate limiting.

## 5. Input Guardrails

Current guardrails detect selected suspicious prompt-injection patterns and redact supported personal information formats. They cannot detect every possible attack or sensitive-data format.

**Future improvement:** Expand detection patterns, add security testing, and introduce additional validation layers.

## 6. Authentication

The current implementation uses API-key authentication rather than individual user accounts.

**Future improvement:** Introduce user registration, secure login, and role-based access control.

## 7. Agent Limitations

The AI agent operates with a bounded number of iterations and a limited set of tools. It may not successfully handle every complex multi-step request.

**Future improvement:** Add more tools, improve error handling, and evaluate agent decisions.

## 8. Performance

External LLM requests can take considerable time, especially when the provider experiences high demand or usage restrictions.

**Future improvement:** Optimize retrieval, reduce unnecessary model calls, and explore streaming responses.

## 9. Evaluation Coverage

The current automated test suite contains six tests. It does not cover every possible user input, retrieval scenario, security issue, or concurrent request.

**Future improvement:** Expand unit, integration, security, and performance testing.

## 10. Deployment Considerations

Production deployment requires appropriate secret management, persistent logging, monitoring, and scalable infrastructure.

**Future improvement:** Introduce centralized monitoring, persistent storage, and production-grade deployment practices.

---

## Conclusion

UniMind AI provides a functional foundation for an academic AI assistant. However, its current implementation has limitations in retrieval quality, security coverage, scalability, and evaluation. These areas are identified as opportunities for future development.