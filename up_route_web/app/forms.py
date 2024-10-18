from django import forms
from django.core.exceptions import ValidationError
import requests


class AddressForm(forms.Form):
    address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Click to enter address',
            'id': 'address-field',
            'class': 'address-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        if not address:
            raise ValidationError("All address fields are required.")

        # Validate the address using Bing Maps API
        if not self.validate_address(address):
            raise ValidationError("Invalid address. Please enter a valid address.")

        return cleaned_data

    def validate_address(self, address):
        api_key = "Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij"
        url = f"http://dev.virtualearth.net/REST/v1/Locations?query={address}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if data['resourceSets'][0]['estimatedTotal'] > 0:
            return True
        return False
    
class RouteParametersForm(forms.Form):
    use_demand = forms.BooleanField(label="Demand", required=False, widget=forms.CheckboxInput())
    use_time_window = forms.BooleanField(label="Scheduling", required=False, widget=forms.CheckboxInput())

    def clean(self):
        cleaned_data = super().clean()
        use_demand = cleaned_data.get('use_demand')
        use_time_window = cleaned_data.get('use_time_window')
        print(f"CLEANED = Use demand: {use_demand}, Use time window: {use_time_window}")
        # if not address:
        #     raise ValidationError("All address fields are required.")

        # Validate the address using Bing Maps API
        # if not self.validate_address(address):
        #     raise ValidationError("Invalid address. Please enter a valid address.")

        return cleaned_data
    
class StartAddressForm(forms.Form):
    address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter start location',
            'id': 'start-location-field',
            'class': 'address-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        if not address:
            raise ValidationError("All address fields are required.")

        # Validate the address using Bing Maps API
        if not self.validate_address(address):
            raise ValidationError("Invalid address. Please enter a valid address.")

        return cleaned_data

    def validate_address(self, address):
        api_key = "Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij"
        url = f"http://dev.virtualearth.net/REST/v1/Locations?query={address}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if data['resourceSets'][0]['estimatedTotal'] > 0:
            return True
        return False
    
class EndAddressForm(forms.Form):
    address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter finish location',
            'id': 'end-location-field',
            'class': 'address-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        if not address:
            raise ValidationError("All address fields are required.")

        # Validate the address using Bing Maps API
        if not self.validate_address(address):
            raise ValidationError("Invalid address. Please enter a valid address.")

        return cleaned_data

    def validate_address(self, address):
        api_key = "Agg3Y0d4Y9AXCgHr7czdzqzmBzyk5GHVJeORQ3hqzdYlxvqA_SpywmgADpXJtJij"
        url = f"http://dev.virtualearth.net/REST/v1/Locations?query={address}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if data['resourceSets'][0]['estimatedTotal'] > 0:
            return True
        return False


