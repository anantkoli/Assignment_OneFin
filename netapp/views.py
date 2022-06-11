from rest_framework.views import APIView
from .serializers import UserSerializer, CollectionSerializer, MovieSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User, Collections, Counts, Movies
import jwt, datetime
import coreapi
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers

# Create your views here.
class RegisterUser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # here we are adding payload for encoding in jwt like expiration of token, and issue at time
        payload = {
            'username': request.data['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'access_token': token
        }

        return response

#this API is used for login the user once again
class LoginUser(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        checkUser = User.objects.filter(username=username)
        if checkUser is None:
            raise AuthenticationFailed('User not found!!!')

        user = User.objects.get(username=username)
        if not user.password == password:
            raise AuthenticationFailed('Incorrect Password!')

        #here we are adding payload for encoding in jwt like expiration of token, and issue at time
        payload = {
            'username': user.username,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat' : datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt' : token
        }

        return response

#this API is for getting the user details like username
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token,  'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.get(username = payload['username'])
        serializer = UserSerializer(user)

        return Response(serializer.data)

#this API for the clear cookies of token
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

#let's define the credy api username and password for the calling thrid party api
CREDY_USERNAME = 'iNd3jDMYRKsN1pjQPMRz2nrq7N99q4Tsp9EY9cM0'
CREDY_PASSWORD = 'Ne5DoTQt7p8qrgkPdtenTK8zd6MorcCR5vXZIJNfJwvfafZfcOs4reyasVYddTyXCz9hcL5FGGIVxw3q02ibnBLhblivqQTp4BIC93LZHj4OppuHQUzwugcYu7TIC5H1'

#this API view for the showing all the movies for the client api link
class LoadMovies(APIView):
    def get(self, request):
        auth = coreapi.auth.BasicAuthentication(
            username=CREDY_USERNAME,
            password=CREDY_PASSWORD
        )
        client = coreapi.Client(auth=auth)
        data = client.get(url='https://demo.credy.in/api/v1/maya/movies/')
        return Response(data)

#This API for loading all the collections
class LoadCollections(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        success = True
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        data = Collections.objects.all()
        serialize = serializers.serialize("json", data)

        myFavGenres = []
        response = Response()
        response.data = {
            "is_success": success,
            "data" : { "collections": serialize},
            "favourite_genres" : myFavGenres
        }
        return response

    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        
        data  = request.data
        collection1 = Collections.objects.create(title=data['title'], description=data['description'])
        collection1.save()

        colid = collection1.id
        for movie in data['movies']:
            movie1 = Movies.objects.create(cid = colid, title=movie['title'], description=movie['description'], genres=movie['genres'], uuid=movie['uuid'])
            movie1.save()

        return Response({
            'collection_uuid': colid
        })

#Below API to load the collections with id, update the collections, and delete the collections
class LoadCollectionItem(APIView):
    def get(self, request, uuid):
        token = request.COOKIES.get('jwt')
        success = True
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            collection1 = Collections.objects.get(id=uuid)
            # serialize = serializers.serialize("json", collection1)
            movies = Movies.objects.filter(cid=uuid)
            serialize = serializers.serialize("json", movies)

        except ObjectDoesNotExist:
            return Response({"is success": False})

        response = Response()
        response.data = {
            "title": collection1.title,
            "description": collection1.description,
            "movies": serialize
        }

        return response

    def put(self, request, uuid):
        data = request.data
        token = request.COOKIES.get('jwt')
        success = True
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            collection1 = Collections.objects.get(id=uuid)
            collection1.title = data['title']
            collection1.description = data['description']
            collection1.save(update_fields=['title', 'description'])

            for movie in data['movies']:
                movie1 = Movies.objects.create(cid=uuid, title=movie['title'], description=movie['description'],
                                               genres=movie['genres'], uuid=movie['uuid'])
                movie1.save()

            movies = Movies.objects.filter(cid=uuid)
            movie_data = MovieSerializer(movies)

        except ObjectDoesNotExist:
            return Response({"is success": False})

        response = Response()
        response.data = {
            "title": data['title'],
            "description": data['description']
        }
        return response

    def delete(self, request, uuid):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        #delete first from the collections
        Collections.objects.filter(id=uuid).delete()
        #delete from movies table with that collections id
        Movies.objects.filter(cid= uuid).delete()

        return Response({
            "message":"success"
        })



#Below API used for the request_counts
class GetCount(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        success = True
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        count = Counts.objects.get(id=1)
        return Response({
            "requests" : count.val
        })

#Below API to reset the counter
class ResetCount(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        success = True
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        Counts.objects.filter(id=1).update(val=0)
        return Response({
            "message": "request count reset successfully"
        })
