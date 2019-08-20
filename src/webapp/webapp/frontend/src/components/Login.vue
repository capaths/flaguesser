<template>
    <v-container>
        <v-app-bar app>
            <v-toolbar-title class="headline text-uppercase">
                <span>Flag</span>
                <span class="font-weight-light">uesser</span>
            </v-toolbar-title>
        </v-app-bar>
        <v-layout
                text-center
                wrap
        >
            <v-card max-width="420" class="mx-auto">
                <v-card-title>
                    Iniciar Sesión
                </v-card-title>
                <v-card-text>
                    <v-form>
                        <v-text-field
                                label="Nombre de usuario"
                                v-model="username"
                                required
                                @keydown.enter.prevent="attemptLogin"
                        ></v-text-field>
                        <v-text-field
                                type="password"
                                label="Contraseña"
                                v-model="password"
                                @keydown.enter.prevent="attemptLogin"
                        ></v-text-field>
                        <v-flex pa-1>
                            <a @click="toggleSignUp">
                                {{signupMode?"¿Ya está registrado?":"Registrarse"}}
                            </a>
                        </v-flex>
                        <v-fade-transition>
                            <v-text-field
                                    type="text"
                                    label="País"
                                    v-model="country"
                                    v-if="signupMode"
                            ></v-text-field>
                        </v-fade-transition>
                        <v-btn class="mr-4" @click="attemptSignup" :disabled="waiting" v-if="signupMode">
                            Enviar
                        </v-btn>
                        <v-btn class="mr-4" @click="attemptLogin" :disabled="waiting" v-else>
                            Ingresar
                        </v-btn>
                    </v-form>
                </v-card-text>
            </v-card>
            <v-snackbar
                    v-model="snackbar"
                    color="error"
                    :timeout=6000
                    :bottom=true
            >
                {{error}}
            </v-snackbar>
        </v-layout>
    </v-container>
</template>

<script lang="ts">
    import Vue from 'vue';
    import {mapState, mapActions} from 'vuex';


    export default Vue.extend({
        name: 'Login',
        data: () => {
            return {
                username: '',
                password: '',
                country: '',
                signupMode: false,
                snackbar: false,
                error: '',
                waiting: false,
            };
        },
        computed: {
            ...mapState('account', ['user']),
        },
        methods: {
            ...mapActions('account', ['login', 'signup']),
            attemptLogin() {
                const credentials = {
                    username: this.username,
                    password: this.password,
                };
                this.waiting = true;
                this.login(credentials)
                    .then(() => {
                        this.waiting = false;
                    })
                    .catch((e: any) => {
                        this.waiting = false;
                        if (e.response.status === 400) {
                            this.showError('Usuario o contraseña incorrecta');
                        } else {
                            this.showError('Error desconocido');
                        }
                    });
            },
            attemptSignup() {
                const credentials = {
                    username: this.username,
                    password: this.password,
                    country: this.country,
                };
                this.waiting = true;
                this.signup(credentials)
                    .then(() => {
                        this.waiting = false;
                    })
                    .catch((e: any) => {
                        this.waiting = false;
                        this.showError('Error desconocido');
                    });
            },
            toggleSignUp() {
                this.signupMode = !this.signupMode;
            },
            showError(msg: string) {
                this.error = msg;
                this.snackbar = true;
            },
        },
    })
    ;
</script>