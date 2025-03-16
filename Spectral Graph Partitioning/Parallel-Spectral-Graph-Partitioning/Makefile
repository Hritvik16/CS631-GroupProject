CXX       = g++
CXXFLAGS  = -std=c++17 -fopenmp

SOURCES = main.cpp \
          src/io_operations.cpp \
          src/laplacian_eigen.cpp \
          src/spectral_operations.cpp

OBJECTS = $(SOURCES:.cpp=.o)

# The final executable name
EXECUTABLE = spectral_partitioning

all: $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $@
	rm -f $(OBJECTS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(EXECUTABLE)
