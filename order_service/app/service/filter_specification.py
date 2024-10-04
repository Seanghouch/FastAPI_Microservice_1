from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session
from order_service.app.db import base
from sqlalchemy import and_, or_, asc, desc
from order_service.app.request.list_request import ListRequest


def get_all_models():
    models = {}
    for table_name, table in base.Base.metadata.tables.items():
        models[table_name] = table
    return models


# Apply individual filter to the query
def apply_filter(query, model, request: ListRequest):
    filter_condition = []

    for filter in request.filters:
        column = getattr(model.c, filter.column, None)
        if column is None:
            raise HTTPException(status_code=404, detail=f"Invalid filter column: {filter.column}")

        if filter.operator == "=":
            condition = (column == filter.value)
        elif filter.operator == "!=":
            condition = (column != filter.value)
        elif filter.operator == ">":
            condition = (column > filter.value)
        elif filter.operator == "<":
            condition = (column < filter.value)
        elif filter.operator == ">=":
            condition = (column >= filter.value)
        elif filter.operator == "<=":
            condition = (column <= filter.value)
        elif filter.operator.upper() == "IN":
            if not isinstance(filter.value, list):
                raise HTTPException(status_code=400, detail=f"The 'in' operator expects a list of values.")
            condition = column.in_(filter.value)
        elif filter.operator.upper() == "NOT_IN":
            if not isinstance(filter.value, list):
                raise HTTPException(status_code=400, detail=f"The 'not in' operator expects a list of values.")
            condition = column.notin_(filter.value)
        elif filter.operator.upper() == "LIKE":
            condition = (column.like(filter.value))
        elif filter.operator.upper() == "NOT_LIKE":
            condition = (column.notlike(filter.value))
        elif filter.operator.upper() == "<DT":
            parsed_datetime = validate_datetime(filter.value)
            condition = (column < parsed_datetime)
        elif filter.operator.upper() == ">DT":
            parsed_datetime = validate_datetime(filter.value)
            condition = (column > parsed_datetime)
        elif filter.operator.upper() == "<=DT":
            parsed_datetime = validate_datetime(filter.value)
            condition = (column <= parsed_datetime)
        elif filter.operator.upper() == ">=DT":
            parsed_datetime = validate_datetime(filter.value)
            condition = (column >= parsed_datetime)
        else:
            raise ValueError(f"Unsupported operator: {filter.operator}")
        filter_condition.append(condition)
    if request.logic.upper() == 'OR':
        data = query.filter(or_(*filter_condition))
    else:
        data = query.filter(and_(*filter_condition))

    return data


def dynamic_search(db: Session, table_name: str, request: ListRequest):
    models = get_all_models()
    table = models.get(table_name)

    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    query = db.query(table)

    # Split the `sort_by` field by commas to support multiple columns
    sort_by_fields = request.sort_by.split(",")

    # Dynamically apply sorting to each field
    for sort_by in sort_by_fields:
        sort_by = sort_by.strip()  # Remove any extra spaces

        if not hasattr(table.columns, sort_by):
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

        # Apply sorting direction
        if request.sort.upper() == 'ASC':
            query = query.order_by(asc(getattr(table.columns, sort_by)))
        else:
            query = query.order_by(desc(getattr(table.columns, sort_by)))

    data = apply_filter(query, table, request).offset(request.skip).limit(request.limit).all()
    return data


def validate_datetime(value):
    if isinstance(value, str):
        try:
            # Try parsing the datetime string into a datetime object
            parsed_datetime = datetime.fromisoformat(value)
            # print(f"Parsed Datetime: {parsed_datetime}")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid datetime format for value: {filter.value}")
    else:
        parsed_datetime = value

    return parsed_datetime
