from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from typing import List, Dict, Any
import re
from models import MODELS


def parse_params(fields: str) -> List[str]:
    """
    Function to parse query string to list of machine readable strings
    :param fields: string comma separated fields with {} delimiters
    :return: a param list
    --------------------------------------------
    Example 1:
    :arg fields = "them, us,you"
    :returns params = ['them', 'us', 'you']
    --------------------------------------------
    Example 2:
    :arg fields = "foo{f, o}, bar{b,r}, boy"
    :returns params = ['boy', 'foo.f', 'foo.o', 'bar.b', 'bar.r']
    --------------------------------------------
    Example 3:
    :arg fields = "eux, nous{moi{m, o, i}, lui{l, u, i{p}}}"
    :returns params = ['eux', 'nous.moi.m', 'nous.moi.o', 'nous.moi.i',
                        'nous.lui.l', 'nous.lui.u', 'nous.lui.i.p']
    """
    
    def add_to_set(key: str, leading: List[str]):
        if key:
            if not re.match(r'^[a-z_]+$', key):
                raise ValueError(f"{key} is not a valid attribute name")
            key = f"{'.'.join(leading)}.{key}" if leading else key
            params.add(key)

    def get_field_end_index(string: str) -> int:
        b_i = string.find("{") + 1
        opened, index = 1, b_i
        for i in range(b_i, len(string)):
            if string[i] == "{":
                opened += 1
            elif string[i] == "}":
                opened -= 1
            if opened == 0:
                index = i
                break
        if opened != 0:
            raise ValueError('Missing closing "}"')
        return index

    def recurrent(string: str, leading: List[str], position: int):
        while string:
            string = string.strip()
            if not string:
                break
                
            key, value = string, None
            index = string.find(",")
            b = string.find("{")

            if index < 0 and b < 0:
                add_to_set(key, leading)
                break
            
            if index >= 0:
                key = string[:index].strip()
                b = key.find("{")

            if b >= 0:
                index = get_field_end_index(string)
                field = string[:index + 1]
                b = field.find("{")
                key = field[:b].strip()
                if not key:
                    raise ValueError('Expecting a string before opened "{"')
                if not field[b + 1:-1].strip():
                    raise ValueError('empty "{}" consider adding values inside')

                leading = [*leading, key] if leading else [key]
                recurrent(field[b + 1:-1], leading, position + 1)
                
                # Move to next field after closing brace
                remaining = string[index + 1:].strip()
                if remaining.startswith(","):
                    string = remaining[1:].strip()
                else:
                    string = remaining
                    
                if len(leading) > position:
                    leading = leading[:position]
            else:
                add_to_set(key, leading)
                if index >= 0:
                    string = string[index + 1:].strip()
                else:
                    break

    params = set()
    if fields:
        recurrent(fields.lower(), [], 0)
        return sorted(list(params))
    return []


def fields_to_query(db: Session, base_model: str, fields: List[str]) -> List[Dict[str, Any]]:
    """
    Function to build and execute SQLAlchemy query based on required fields.
    Uses modern SQLAlchemy 2.0+ syntax with select() and eager loading.
    
    :param db: SQLAlchemy session
    :param base_model: The base model name (e.g., 'orders')
    :param fields: fields to include in the query with dot notation format
    :return: List of dictionaries with requested data
    """
    
    if base_model not in MODELS:
        raise AttributeError(f"model '{base_model}' does not exist")
    
    model_class = MODELS[base_model]
    
    # Relationship name mapping from plural to singular
    relationship_mapping = {
        'users': 'user',
        'products': 'product', 
        'addresses': 'address',
        'orders': 'order'
    }
    
    # Process fields to handle base model prefix and relationship mapping
    processed_fields = []
    for field in fields:
        parts = field.split('.')
        # If field starts with base model name, remove it
        if parts[0] == base_model:
            parts = parts[1:]
        
        # Map plural relationship names to singular
        if len(parts) > 0 and parts[0] in relationship_mapping:
            parts[0] = relationship_mapping[parts[0]]
            
        if parts:  # Only add if there are remaining parts
            processed_fields.append('.'.join(parts))
    
    # Build eager loading options based on processed fields
    options = []
    relationship_fields = set()
    
    for field in processed_fields:
        parts = field.split('.')
        if len(parts) > 1:
            # This is a relationship field
            rel_name = parts[0]
            if hasattr(model_class, rel_name):
                relationship_fields.add(rel_name)
                
    # Add selectinload for each relationship
    for rel_name in relationship_fields:
        options.append(selectinload(getattr(model_class, rel_name)))
    
    # Execute query
    stmt = select(model_class).options(*options)
    result = db.execute(stmt).scalars().all()
    
    # Build response based on requested fields
    response = []
    for item in result:
        item_dict = {}
        
        for field in processed_fields:
            parts = field.split('.')
            current_obj = item
            current_dict = item_dict
            
            # Navigate through the object hierarchy
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # Last part - set the value
                    if hasattr(current_obj, part):
                        current_dict[part] = getattr(current_obj, part)
                else:
                    # Intermediate part - navigate deeper
                    if hasattr(current_obj, part):
                        related_obj = getattr(current_obj, part)
                        if related_obj is not None:
                            if part not in current_dict:
                                current_dict[part] = {}
                            current_dict = current_dict[part]
                            current_obj = related_obj
                        else:
                            break
                    else:
                        break
        
        response.append(item_dict)
    
    return response


# API wrapper functions
def parse_params_api(params: str) -> List[str]:
    """API wrapper for parse_params with error handling"""
    try:
        fields = parse_params(params)
        return fields
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))


def fields_to_query_api(db: Session, base_model: str, fields: List[str]) -> List[Dict[str, Any]]:
    """API wrapper for fields_to_query with error handling"""
    try:
        result = fields_to_query(db, base_model, fields)
        return result
    except AttributeError as ex:
        raise HTTPException(status_code=400, detail=str(ex))