admin = User(name="admin", email="admin@localhost", role_id=1, password=current_app.config["ADMIN_PASS"])
op.bulk_insert(
    user_table, [
        {
            'name': admin.name,
            'email': admin.email,
            'password_hash': admin.password_hash,
            'role_id': admin.role_id,
        },
    ])