import postcar


class Migration(postcar.Migration):
    def get_forward(self) -> str:
        return """
            create extension pg_trgm;
        """

    def get_rollback(self) -> str:
        return """
            drop extension pg_trgm;
        """
