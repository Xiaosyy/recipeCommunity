from recipeshare import create_app


def test_terms_of_service_page_renders_botanical_design(client):
    response = client.get("/terms")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Terms of Service" in html
    assert "Acceptance of Terms" in html
    assert "Use of the Website" in html
    assert "Account Responsibility" in html
    assert "Community Guidelines" in html
    assert "Back to home" in html
    assert "legal-backdrop" in html
    assert "legal-divider" in html


def test_privacy_policy_page_renders_botanical_design(client):
    response = client.get("/privacy")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Privacy Policy" in html
    assert "Information We Collect" in html
    assert "How We Use Your Information" in html
    assert "How We Protect Your Information" in html
    assert "Sharing of Information" in html
    assert "Your Rights" in html
    assert "Contact Us" in html
    assert "support@recipeshare.com" in html
    assert "We are committed to keeping your information safe and secure." in html
    assert "Back to Home" in html


def test_spa_pages_terms_and_privacy(client):
    terms_spa = client.get("/api/v1/ui/pages/terms")
    assert terms_spa.status_code == 200
    terms_html = terms_spa.get_data(as_text=True)
    assert "Terms of Service" in terms_html
    assert "Acceptance of Terms" in terms_html

    privacy_spa = client.get("/api/v1/ui/pages/privacy")
    assert privacy_spa.status_code == 200
    privacy_html = privacy_spa.get_data(as_text=True)
    assert "Privacy Policy" in privacy_html
    assert "We are committed to keeping your information safe and secure." in privacy_html

