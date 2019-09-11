<template>
    <v-container fluid grid-list-md :fill-height="true" pa-0 ma-0>
        <v-layout row wrap>
            <v-flex d-flex md2 xs4 pa-0>
                <Profile></Profile>
            </v-flex>
            <v-flex d-flex md6 xs6 pa-0>
                <Game></Game>
            </v-flex>
            <v-flex d-flex md4 xs2 pa-0>
                <Chat></Chat>
            </v-flex>
        </v-layout>
    </v-container>
</template>

<script>
    import Profile from './menu/Profile';
    import Chat from './menu/Chat';
    import Game from './Game';

    import {mapState} from 'vuex';

    export default {
        name: 'Menu',
        components: {
            Chat,
            Profile,
            Game,
        },
        computed: {
            ...mapState('account', ['user']),
        },
        beforeMount() {
            this.$options.sockets.onopen = () => {
                this.$socket.sendObj({
                    method: 'identify',
                    data: {
                        guess: this.user.username,
                    },
                });
            };
        },
        mounted() {
            this.$options.sockets.onmessage = (message) => {
                const data = JSON.parse(message.data);
                if (data.type === 'event') {
                    console.log(data.event + " - " + JSON.stringify(data.data));
                }
            };
        },
    };
</script>

<style scoped>

</style>