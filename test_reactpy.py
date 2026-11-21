import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edugrade.settings')
django.setup()

from django.test import Client
from django.template.loader import render_to_string

def test_reactpy_render():
    print("Testing ReactPy host template rendering...")
    html_out = render_to_string('reactpy_index.html')
    assert '<body' in html_out
    assert 'EduGrade AI' in html_out
    assert 'reactpy' in html_out.lower()
    print("[PASS] reactpy_index.html rendered successfully with ReactPy tag.")

    print("\nTesting Django Client GET / with ReactPy...")
    client = Client()
    resp = client.get('/')
    print("Response status code:", resp.status_code)
    assert resp.status_code == 200
    print("[PASS] Root GET / returned HTTP 200.")

    print("\nAll ReactPy rendering tests PASSED successfully!")

if __name__ == '__main__':
    test_reactpy_render()
