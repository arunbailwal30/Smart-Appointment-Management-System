document.getElementById('dropdown').addEventListener('change', function() {
    const selectedValue = this.value;
    const positionInput = document.getElementById('position');
    const positionLabel = document.getElementById('lpos');
    
    const isEmployee = selectedValue === 'Employee';
    positionInput.style.display = isEmployee ? 'block' : 'none';
    positionLabel.style.display = isEmployee ? 'block' : 'none';
});