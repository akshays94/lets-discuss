from rest_framework import serializers
from .models import User, UserReputation, UserMeta


class UserSerializer(serializers.ModelSerializer):

    score = serializers.SerializerMethodField()

    def get_score(self, obj):
      meta = obj.usermeta_set.all().first()
      if meta: 
        return meta.score 
      return None

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'score')
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token',)
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}



class UserReputationSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    created_by = UserSerializer()
    category_txt = serializers.CharField(source='get_category_display')
    instance = serializers.ReadOnlyField()

    class Meta:
        model = UserReputation
        fields = ('id', 'points', 'user', 'category', 'category_txt', 'created_by', 'instance')


class UserMetaSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = UserMeta
        fields = ('id', 'user', 'score')
