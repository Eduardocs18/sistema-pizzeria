function mostrarSeccion(id){

    const secciones = document.querySelectorAll('.seccion')

    secciones.forEach(seccion => {
        seccion.classList.add('oculto')
    })

    document.getElementById(id).classList.remove('oculto')
}