function mostrarSeccion(id){

    const secciones = document.querySelectorAll('.seccion')

    secciones.forEach(seccion => {
        seccion.classList.add('oculto')
    })

    document.getElementById(id).classList.remove('oculto')
}

const pizzaSelect = document.querySelector(
    'select[name="pizza_id"]'
);

const tamanoSelect = document.getElementById(
    'tamanoPizza'
);

const precioInput = document.getElementById(
    'precioPizza'
);

const cantidadInput = document.getElementById(
    'cantidadPizza'
);

const adicionalSelect = document.getElementById(
    'adicionalPizza'
);

function actualizarPrecio() {

    const option =
        pizzaSelect.options[pizzaSelect.selectedIndex];

    const tamano =
        tamanoSelect.value;

    const adicional =
        adicionalSelect.value;

    let precio = 0;

    if (tamano === 'Personal') {

        precio = Number(option.dataset.personal);

    }

    else if (tamano === 'Small') {

        precio = Number(option.dataset.small);

    }

    else if (tamano === 'Mediana') {

        precio = Number(option.dataset.mediana);

    }

    else {

        precio = Number(option.dataset.familiar);

    }

    let valorAdicional = 0;

    if (adicional === 'queso') {

        if (tamano === 'Personal')
            valorAdicional = 4000;
        else if (tamano === 'Small')
            valorAdicional = 8000;
        else if (tamano === 'Mediana')
            valorAdicional = 12000;
        else
            valorAdicional = 16000;

    }

    else if (
        adicional === 'papita' ||
        adicional === 'pollo'
    ) {

        if (tamano === 'Personal')
            valorAdicional = 5000;
        else if (tamano === 'Small')
            valorAdicional = 10000;
        else if (tamano === 'Mediana')
            valorAdicional = 15000;
        else
            valorAdicional = 20000;

    }

    else if (adicional === 'vegetales') {

        if (tamano === 'Personal')
            valorAdicional = 4000;
        else if (tamano === 'Small')
            valorAdicional = 8000;
        else if (tamano === 'Mediana')
            valorAdicional = 12000;
        else
            valorAdicional = 16000;

    }

    const cantidad =
        Number(cantidadInput.value) || 1;

    const total =
        (precio + valorAdicional) * cantidad;

    precioInput.value =
        '$' + total.toLocaleString('es-CO');
}

pizzaSelect.addEventListener(
    'change',
    actualizarPrecio
);

tamanoSelect.addEventListener(
    'change',
    actualizarPrecio
);

cantidadInput.addEventListener(
    'input',
    actualizarPrecio
);

adicionalSelect.addEventListener(
    'change',
    actualizarPrecio
);

actualizarPrecio();

window.addEventListener('load', () => {

    const hash = window.location.hash;

    if(hash){

        const id = hash.replace('#', '');

        const seccion = document.getElementById(id);

        if(seccion){

            mostrarSeccion(id);

        }

    }

});