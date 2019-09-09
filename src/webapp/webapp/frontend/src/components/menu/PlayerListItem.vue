<template>
    <v-list-item width="100%" link @click="challenge">
        <v-list-item-avatar>
            <v-img :src="avatar"></v-img>
        </v-list-item-avatar>
        <v-list-item-content>
            <v-list-item-title v-text="username"></v-list-item-title>
            <v-list-item-subtitle v-text="country + '-' + elo"></v-list-item-subtitle>
        </v-list-item-content>
        <v-spacer>
        </v-spacer>
        <v-list-item-action v-if="challenged">
            <p>Challenge Complete!</p>
        </v-list-item-action>
    </v-list-item>
</template>

<script>
    export default {
        name: 'PlayerListItem',
        data() {
            return {
                challenged: false,
            };
        },
        props: [
            'username',
            'country',
            'elo',
            'avatar',
        ],
        methods: {
            challenge() {
                if (!this.challenged) {
                    this.challenged = true;
                    this.$socket.sendObj({
                        'method': 'challenge',
                        'data': {
                            'challenged': this.username,
                        },
                    })
                }
            },
        },
    };
</script>

<style scoped>

</style>