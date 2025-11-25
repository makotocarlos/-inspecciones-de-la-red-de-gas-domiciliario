"""
Database Optimization Utilities
Professional database query optimization and monitoring tools.
"""

from django.db import connection
from django.db.models import Prefetch
from functools import wraps
import time
import logging

logger = logging.getLogger('performance')


def log_queries(func):
    """
    Decorator to log all database queries executed by a function.
    Useful for development and identifying N+1 query problems.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django.conf import settings
        
        if not settings.DEBUG:
            return func(*args, **kwargs)
        
        # Reset queries
        connection.queries_log.clear()
        
        # Execute function
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Log queries
        query_count = len(connection.queries)
        total_time = sum(float(q['time']) for q in connection.queries)
        
        logger.info(
            f"{func.__name__}: {query_count} queries in {end_time - start_time:.2f}s "
            f"(DB time: {total_time:.2f}s)"
        )
        
        # Log slow queries
        for query in connection.queries:
            if float(query['time']) > 0.1:  # 100ms
                logger.warning(f"Slow query ({query['time']}s): {query['sql'][:200]}")
        
        return result
    
    return wrapper


def query_debugger(queryset):
    """
    Print the SQL query that will be executed by a QuerySet.
    
    Usage:
        query_debugger(User.objects.filter(is_active=True))
    """
    from django.conf import settings
    
    if settings.DEBUG:
        print("\n" + "="*80)
        print("QUERY DEBUG")
        print("="*80)
        print(queryset.query)
        print("="*80 + "\n")
    
    return queryset


class QueryCounter:
    """
    Context manager to count and log queries executed in a code block.
    
    Usage:
        with QueryCounter() as counter:
            # Your code here
            users = User.objects.all()
        print(f"Executed {counter.count} queries")
    """
    
    def __init__(self, log_queries=False):
        self.log_queries = log_queries
        self.count = 0
        self.initial_count = 0
    
    def __enter__(self):
        self.initial_count = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.count = len(connection.queries) - self.initial_count
        
        if self.log_queries:
            logger.info(f"Executed {self.count} queries")
            
            for i, query in enumerate(connection.queries[self.initial_count:], 1):
                logger.debug(f"Query {i}: {query['sql'][:200]}")


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """
    Optimize a queryset with select_related and prefetch_related.
    
    Args:
        queryset: The base queryset
        select_related: List of fields for select_related
        prefetch_related: List of fields for prefetch_related
    
    Returns:
        Optimized queryset
    
    Example:
        queryset = optimize_queryset(
            Inspection.objects.all(),
            select_related=['user', 'inspector'],
            prefetch_related=['items', 'photos']
        )
    """
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset


def bulk_create_with_return(model, objects, batch_size=1000):
    """
    Bulk create objects and return them with IDs.
    
    Args:
        model: The Django model class
        objects: List of model instances
        batch_size: Number of objects to create per batch
    
    Returns:
        List of created objects with IDs
    """
    return model.objects.bulk_create(
        objects,
        batch_size=batch_size,
        ignore_conflicts=False
    )


def bulk_update_optimized(queryset, field_updates, batch_size=1000):
    """
    Efficiently update multiple objects at once.
    
    Args:
        queryset: QuerySet of objects to update
        field_updates: Dict of field names and values to update
        batch_size: Number of objects to update per batch
    
    Example:
        bulk_update_optimized(
            User.objects.filter(is_active=False),
            {'status': 'inactive', 'updated_at': timezone.now()}
        )
    """
    return queryset.update(**field_updates)


class DatabaseRouter:
    """
    Database router for read/write splitting.
    Configure in settings.py: DATABASE_ROUTERS = ['core.utils.db.DatabaseRouter']
    """
    
    def db_for_read(self, model, **hints):
        """Send read operations to read replica if available."""
        return 'read_replica' if 'read_replica' in settings.DATABASES else 'default'
    
    def db_for_write(self, model, **hints):
        """Send write operations to primary database."""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both objects are in the same database."""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure migrations only run on primary database."""
        return db == 'default'


def get_or_create_optimized(model, defaults=None, **kwargs):
    """
    Optimized version of get_or_create that uses select_for_update.
    Prevents race conditions in high-concurrency scenarios.
    
    Args:
        model: Django model class
        defaults: Default values for creation
        **kwargs: Lookup parameters
    
    Returns:
        Tuple of (object, created)
    """
    from django.db import transaction
    
    with transaction.atomic():
        try:
            obj = model.objects.select_for_update().get(**kwargs)
            return obj, False
        except model.DoesNotExist:
            params = {**kwargs, **(defaults or {})}
            obj = model.objects.create(**params)
            return obj, True


def execute_raw_sql(sql, params=None, fetch_all=True):
    """
    Execute raw SQL safely with parameter binding.
    
    Args:
        sql: SQL query string with %s placeholders
        params: Tuple of parameters to bind
        fetch_all: If True, return all rows; if False, return cursor
    
    Returns:
        List of rows or cursor
    
    Example:
        results = execute_raw_sql(
            "SELECT * FROM users WHERE age > %s",
            (18,)
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        
        if fetch_all:
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        
        return cursor


def explain_query(queryset):
    """
    Get the EXPLAIN output for a queryset to analyze query performance.
    Only works with PostgreSQL.
    
    Args:
        queryset: Django QuerySet
    
    Returns:
        Query execution plan
    """
    sql, params = queryset.query.sql_with_params()
    
    with connection.cursor() as cursor:
        cursor.execute(f"EXPLAIN ANALYZE {sql}", params)
        return cursor.fetchall()


# Index suggestions based on common queries
SUGGESTED_INDEXES = """
-- Performance Optimization: Suggested Database Indexes

-- Users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users_customuser(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users_customuser(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users_customuser(is_active);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users_customuser(role, is_active);

-- Inspections table
CREATE INDEX IF NOT EXISTS idx_inspections_user ON inspections_inspection(user_id);
CREATE INDEX IF NOT EXISTS idx_inspections_inspector ON inspections_inspection(inspector_id);
CREATE INDEX IF NOT EXISTS idx_inspections_status ON inspections_inspection(status);
CREATE INDEX IF NOT EXISTS idx_inspections_date ON inspections_inspection(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_inspections_created ON inspections_inspection(created_at);
CREATE INDEX IF NOT EXISTS idx_inspections_status_date ON inspections_inspection(status, scheduled_date);

-- Reports table
CREATE INDEX IF NOT EXISTS idx_reports_inspection ON reports_report(inspection_id);
CREATE INDEX IF NOT EXISTS idx_reports_user ON reports_report(generated_by_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports_report(status);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports_report(created_at);

-- Notifications table
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications_notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications_notification(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications_notification(status);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications_notification(read_at);
CREATE INDEX IF NOT EXISTS idx_notifications_user_status ON notifications_notification(user_id, status);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_inspections_user_status_date 
    ON inspections_inspection(user_id, status, scheduled_date DESC);
CREATE INDEX IF NOT EXISTS idx_inspections_inspector_status_date 
    ON inspections_inspection(inspector_id, status, scheduled_date DESC);
"""


def apply_suggested_indexes():
    """
    Apply suggested database indexes for better performance.
    Run this in production after deployment.
    """
    with connection.cursor() as cursor:
        for statement in SUGGESTED_INDEXES.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    logger.info(f"Applied index: {statement[:100]}")
                except Exception as e:
                    logger.error(f"Failed to apply index: {e}")
