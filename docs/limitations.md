# Limitations

This tool serves as a lightweight and transparent baseline for evaluating prompt injection vulnerabilities. It is not intended to function as a comprehensive security assessment solution.


## Detection Limitations

- **Paraphrased or indirect disclosures.** Detection is limited to predefined representations of the canary, including plain text, separated text, reversed text, ROT13, hexadecimal, and Base64 encodings. If a model reveals the secret through paraphrasing or indirect descriptions, the disclosure may not be detected.
- **Multi-turn leakage.** Each attack is evaluated within a single message. Consequently, prompt injection attempts that extract information gradually across multiple interactions are not assessed.
- **Unsupported encodings and transformations.** Detection is restricted to the implemented variants. Alternative representations, such as Morse code or translations into other languages, are not currently identified.

## Evaluation Scope

- The attack prompts are static and written in English. They do not adapt dynamically in response to model outputs.

- Indirect prompt injection scenarios are simulated by embedding hidden instructions directly within the prompt. Therefore, the tool does not evaluate vulnerabilities in real-world retrieval-augmented generation (RAG) or document retrieval pipelines.

- Only text-based JSON chat endpoints are supported.

- The assessment focuses exclusively on secret and instruction leakage. Other risks, including harmful content generation, tool misuse, and broader data exfiltration concerns, are outside the scope of evaluation.

## Interpreting Results

- The included demonstration bot is rule-based. Its purpose is to validate the functionality of the tool rather than reflect the security posture of a real language model.

- The attack library contains 15 attacks, with three attacks per category. As a result, the findings should be interpreted as illustrative examples rather than statistically representative results.

- Language models are inherently non-deterministic. An attack that is successfully mitigated in one execution may lead to leakage in another. Running multiple scans and comparing timestamped reports can provide a more reliable assessment.

- Successfully passing all available attacks should not be interpreted as evidence that a system is secure.

## Safe and Responsible Use

- Only test systems that you own or have explicit permission to assess, and use synthetic canary values during testing.

- Generated reports contain complete model responses and should therefore be treated as sensitive. To reduce the risk of accidental disclosure, the reports/ directory is excluded from version control.

- Avoid providing real API keys through command-line arguments, as command histories may retain them and unintentionally expose sensitive credentials.