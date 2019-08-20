<template>
    <v-list-item width="100%" link @click="challenge">
        <v-list-item-avatar>
            <v-img :src="avatar"></v-img>
        </v-list-item-avatar>
        <v-list-item-content>
            <v-list-item-title v-text="username"></v-list-item-title>
            <v-list-item-subtitle v-text="country"></v-list-item-subtitle>
        </v-list-item-content>
        <v-spacer>
        </v-spacer>
        <v-list-item-action v-if="challenged">
            <v-btn>Challenge sent!</v-btn>
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
                }
            },
        },
    };
</script>

<style scoped>

</style>