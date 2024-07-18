# # order_utils.py

# import logging

# logger = logging.getLogger(__name__)

# class OrderUtils:
#     def __init__(self, file_path):
#         self.file_path = file_path

#     def read_order_numbers(self):
#         order_numbers = []
#         with open(self.file_path, 'r') as file:
#             for line in file:
#                 if 'order-no' in line:
#                     order_number = line.split('order-no: ')[1].split(',')[0].strip()
#                     if order_number not in order_numbers:
#                         order_numbers.append(order_number)
#         return order_numbers

#     @staticmethod
#     def select_order_number(event, callback=None):
#         selected_order = event.widget.get()
#         if callback:
#             callback(selected_order)

import logging

logger = logging.getLogger(__name__)

class OrderUtils:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_order_numbers(self):
        order_numbers = []
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    if 'order-no' in line:
                        order_number = line.split('order-no: ')[1].split(',')[0].strip()
                        if order_number not in order_numbers:
                            order_numbers.append(order_number)
        except FileNotFoundError as e:
            logger.error(f"File not found: {self.file_path}")
            # Handle the error, maybe raise or return an empty list
            return []
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            # Handle other exceptions as needed
            return []

        return order_numbers

    def get_order_numbers(self):
        return self.read_order_numbers()

    def get_selected_order(self, event):
        selected_order = event.widget.get()
        return selected_order
