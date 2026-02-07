package ai_middleware.policy

default allow = true
default reason = ""

# Block if SQL keywords are present
deny[msg] {
    keywords := ["SELECT", "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "GRANT", "REVOKE", "UNION"]
    some i
    contains(upper(input.text), keywords[i])
    msg := sprintf("Blocked due to SQL keyword: %v", [keywords[i]])
}

# Block if jailbreak phrase
deny[msg] {
    contains(lower(input.text), "ignore previous instructions")
    msg := "Blocked due to jailbreak attempt"
}

# Main decision logic
allow = false {
    count(deny) > 0
}

reason = msg {
    msg := deny[_]
}
