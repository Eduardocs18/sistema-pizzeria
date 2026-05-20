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

function actualizarPrecio() {

    const option =
        pizzaSelect.options[pizzaSelect.selectedIndex];

    const tamano = tamanoSelect.value;

    let precio = 0;

    if (tamano === 'Personal') {
        precio = option.dataset.personal;
    }

    else if (tamano === 'Small') {
        precio = option.dataset.small;
    }

    else if (tamano === 'Mediana') {
        precio = option.dataset.mediana;
    }

    else {
        precio = option.dataset.familiar;
    }

    precioInput.value = '$' + precio;
}

pizzaSelect.addEventListener(
    'change',
    actualizarPrecio
);

tamanoSelect.addEventListener(
    'change',
    actualizarPrecio
);

actualizarPrecio();