def get_all_clients():
    """
        Get all clients in DB
    """
    with Session(engine) as session:
        branch = org_db_schema.get_branch_table()
        result = session.query(branch.id_branch).filter(branch.id_organization == id_detail).all()
        return [row[0] for row in result] 