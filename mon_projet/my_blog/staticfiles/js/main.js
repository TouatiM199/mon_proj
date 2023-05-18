<script>
function addInstructeur() {
    var nom_instructeur = prompt("Entrez le nom de l'instructeur:");
    if (nom_instructeur != null) {
        var option = document.createElement("option");
        option.text = nom_instructeur;
        option.value = nom_instructeur;
        var select = document.getElementById("id_instructeur");
        select.add(option);
    }
}
</script>
<script>
function deleteInstructeur() {
    var select = document.getElementById("id_instructeur");
    var selectedOption = select.options[select.selectedIndex];
    if (selectedOption != null) {
        select.remove(selectedOption.index);
    }
}
</script>



