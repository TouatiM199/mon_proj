// Récupère les éléments HTML
const select = document.querySelector('.dropdown select');
const add = document.querySelector('.dropdown button.add');
const remove = document.querySelector('.dropdown button.remove');
// Fonction pour ajouter une option au menu déroulant
function addInstructeur() {
    var new_instructeur = prompt("Entrez le nom de l'instructeur:");
    if (new_instructeur != null) {
        var option = document.createElement("option");
        option.text = new_instructeur;
        option.value = new_instructeur;
        var select = document.getElementById("instructeur_id");
        select.add(option);
    }
}
// Fonction pour supprimer l'option sélectionnée du menu déroulant
function deleteInstructeur() {
    var select = document.getElementById("instructeur_id");
    var selectedOption = select.options[select.selectedIndex];
    if (selectedOption != null) {
        select.remove(selectedOption.index);
    }
}

// Ajoute des écouteurs d'événements pour les boutons
add.addEventListener('click', addInstructeur);
remove.addEventListener('click', deleteInstructeur);


