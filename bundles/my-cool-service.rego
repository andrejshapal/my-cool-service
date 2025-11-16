package httpapi.authz

default allow := false

allow if {
	input.method == "GET"
	input.path == ["api", "users"]
	input.role in ["admin", "editor"]
}

allow if {
	input.method == "POST"
	input.path == ["api", "users"]
	input.role == "admin"
}
