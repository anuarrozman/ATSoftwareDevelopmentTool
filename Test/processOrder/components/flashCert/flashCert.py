# components/flashCert/flashCert.py

used_cert_ids = set()  # Track used cert-ids

def get_cert_ids_for_order(orders, selected_order_no):
    cert_ids = [order['esp-secure-cert-partition'] for order in orders if order['order-no'] == selected_order_no]
    return cert_ids

def flash_certificate(cert_id):
    if cert_id in used_cert_ids:
        print(f"Cert ID {cert_id} has already been used.")
        return False

    print(f"Flashing certificate with cert-id: {cert_id}")
    # Simulate flashing the certificate
    used_cert_ids.add(cert_id)
    return True

def get_remaining_cert_ids(cert_ids):
    return [cert_id for cert_id in cert_ids if cert_id not in used_cert_ids]
