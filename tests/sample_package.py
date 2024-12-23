from typing import List
def function_with_three_arguments(name: str, age: int, lucky_numbers: List[int]) -> bool:
    '''
    Args:
        name (str): The name of the person.
        age (int): The age of the person.
        lucky_numbers (List[int]): A list of the person's lucky numbers.

    Returns:
        bool: If the person is in luck today.
    '''
    return True

def function_with_just_a_desc(name: str, age: int) -> bool:
    '''
    Simplre desc
    '''
    return False

def bad_function1(name: str, age: int) -> bool:
    '''
    Args:
        name (str): The name of the person.
        age (int): The age of the person.
        lucky_numbers (List[int]): A list of the person's lucky numbers.

    Returns:
        bool: If the person is in luck today.
    '''
    pass